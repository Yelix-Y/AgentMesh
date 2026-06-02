import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from agentmesh.db.database import init_db
from agentmesh.models.loader import load_profile, load_profiles_from_dir
from agentmesh.bus.message_bus import MessageBus
from agentmesh.memory.store import MemoryStore
from agentmesh.runtime.state_machine import AgentStateMachine
from agentmesh.runtime.supervisor import Supervisor

app = typer.Typer(
    name="agentmesh",
    help="AgentMesh — AI Organization Simulator. Digital coworkers that collaborate through natural language.",
    no_args_is_help=True,
)
agent_app = typer.Typer(help="Agent commands")
app.add_typer(agent_app, name="agent")

console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    init_db()


@agent_app.command("load")
def agent_load(profile: Path = typer.Argument(..., help="Path to agent YAML profile")):
    """Load and validate an agent profile."""
    init_db()
    try:
        p = load_profile(profile)
        table = Table(title=f"Agent Profile: {p.name}", show_header=True)
        table.add_column("Field", style="bold cyan")
        table.add_column("Value")
        table.add_row("Name", p.name)
        table.add_row("Role", p.role)
        table.add_row("Personality", p.personality)
        table.add_row("Working Style", p.working_style)
        table.add_row("Specialization", p.specialization)
        table.add_row("LLM Provider", p.llm_backend.provider)
        table.add_row("LLM Model", p.llm_backend.model)
        table.add_row("Worker", p.worker.type)
        console.print(table)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        raise typer.Exit(1)


@agent_app.command("status")
def agent_status(name: str = typer.Argument(..., help="Agent name")):
    """Show current state and inbox for an agent."""
    init_db()
    sm = AgentStateMachine(name)
    bus = MessageBus()
    unread = bus.poll(name)

    table = Table(title=f"Agent Status: {name}")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")
    table.add_row("State", f"[green]{sm.state.value}[/green]")
    table.add_row("Unread Messages", str(len(unread)))
    if unread:
        last = unread[-1]
        table.add_row("Latest Message From", last.sender_id)
        table.add_row("Latest Message Type", last.message_type.value)
    console.print(table)


@agent_app.command("message")
def agent_message(
    name: str = typer.Argument(..., help="Agent name to send message to"),
    text: str = typer.Argument(..., help="Message text"),
):
    """Inject a message from the human operator to an agent."""
    init_db()
    from agentmesh.models.message import ACPMessage, MessageType
    bus = MessageBus()
    msg = ACPMessage(
        sender_id="human",
        recipient_id=name,
        message_type=MessageType.HUMAN_INTERVENTION,
        body=text,
    )
    bus.publish(msg)
    console.print(f"[green]✓[/green] Message delivered to [bold]{name}[/bold]")


@app.command("watch")
def watch(interval: float = typer.Option(1.0, help="Poll interval in seconds")):
    """Stream the live message feed between agents."""
    import time
    init_db()
    from agentmesh.db.database import get_connection

    seen_ids: set[str] = set()
    console.print("[bold cyan]AgentMesh[/bold cyan] — watching message stream (Ctrl+C to stop)\n")

    TYPE_COLORS = {
        "TASK_HANDOFF": "yellow",
        "COMPLETION_REPORT": "green",
        "REVIEW_DECISION": "bold green",
        "REJECTION": "red",
        "ESCALATION": "bold red",
        "CLARIFICATION_REQUEST": "blue",
        "STATUS_UPDATE": "dim",
        "REVIEW_REQUEST": "magenta",
        "HUMAN_INTERVENTION": "bold white",
    }

    try:
        while True:
            with get_connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM messages ORDER BY created_at ASC"
                ).fetchall()
            for row in rows:
                if row["id"] not in seen_ids:
                    seen_ids.add(row["id"])
                    color = TYPE_COLORS.get(row["message_type"], "white")
                    ts = row["created_at"][:19].replace("T", " ")
                    console.print(
                        f"[dim]{ts}[/dim]  "
                        f"[bold]{row['sender_id']}[/bold] → [bold]{row['recipient_id']}[/bold]  "
                        f"[{color}]{row['message_type']}[/{color}]\n"
                        f"  [dim]{row['body'][:120]}{'...' if len(row['body']) > 120 else ''}[/dim]"
                    )
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]Stream closed.[/dim]")


@app.command("run")
def run(
    task: str = typer.Argument(..., help="The task to hand to the developer"),
    agents_dir: Path = typer.Option(Path("agents"), "--agents-dir", help="Directory of agent YAML profiles"),
    max_steps: int = typer.Option(50, "--max-steps", help="Safety cap on supervisor steps"),
    session: str = typer.Option("default", "--session", help="Session id for the event log"),
    provider: str = typer.Option("mock", "--provider", help="LLM provider: 'mock' (no API key) or 'anthropic'"),
):
    """Submit a task and run the whole organization until it goes quiet."""
    import uuid
    from agentmesh.models.message import ACPMessage, MessageType
    from agentmesh.runtime.llm import MockLLMProvider

    init_db()
    profiles = load_profiles_from_dir(agents_dir)
    if not profiles:
        console.print(f"[red]Error:[/red] no agent profiles found in {agents_dir}")
        raise typer.Exit(1)

    llm = MockLLMProvider() if provider == "mock" else None

    thread_id = str(uuid.uuid4())
    bus = MessageBus()
    bus.publish(ACPMessage(
        thread_id=thread_id,
        sender_id="human",
        recipient_id="developer",
        message_type=MessageType.HUMAN_INTERVENTION,
        body=task,
    ))

    console.print(f"[bold cyan]AgentMesh[/bold cyan] — running task: [bold]{task}[/bold]\n")
    result = Supervisor(profiles, session_id=session, llm=llm).run(max_steps=max_steps)

    thread = bus.get_thread(thread_id)
    for m in thread:
        ts = m.created_at.isoformat()[11:19]
        console.print(
            f"[dim]{ts}[/dim]  [bold]{m.sender_id}[/bold] → [bold]{m.recipient_id}[/bold]  "
            f"[yellow]{m.message_type.value}[/yellow]\n  [dim]{m.body}[/dim]"
        )

    status = "[green]quiescent[/green]" if result.quiescent else "[red]hit max-steps[/red]"
    console.print(
        f"\n{status} — {result.steps} steps, {result.messages_published} messages exchanged."
    )


if __name__ == "__main__":
    app()
