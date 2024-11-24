from models import JsonManager, TodoStatus
import argparse

STATUS_TO_EMOJIS = {
    TodoStatus.TODO: "🔴",
    TodoStatus.IN_PROGRESS: "🟠",
    TodoStatus.DONE: "🟢",
}


def make_table(headers: list[str], rows: list[list[str]]) -> str:
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]

    border = "+".join("-" * (w + 2) for w in col_widths)
    border = f"+{border}+"

    def format_row(row):
        return (
            "|"
            + "|".join(f" {str(item).ljust(w)} " for item, w in zip(row, col_widths))
            + "|"
        )

    table = [border, format_row(headers), border]
    for row in rows:
        table.append(format_row(row))
    table.append(border)

    return "\n".join(table)


def main():
    parser = argparse.ArgumentParser(description="Task CLI")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # List
    list_todos = subparsers.add_parser("list", help="List tasks")
    list_todos.add_argument(
        "status",
        choices=[status.value for status in TodoStatus],
        help="Filter by status",
        default=None,
        nargs="?",
    )
    # Add
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("description", type=str, help="Description of the task")

    # Status
    mark_progress = subparsers.add_parser(
        "mark-in-progress", help="Mark a task as in progress"
    )
    mark_done = subparsers.add_parser("mark-done", help="Mark a task as done")
    mark_progress.add_argument("id", type=int, help="ID of the task")
    mark_done.add_argument("id", type=int, help="ID of the task")
    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="ID of the task")
    args = parser.parse_args()

    match args.command:
        case "list":
            todos = manager.get_all()
            if args.status is not None:
                todos = manager.get_all_by_status(TodoStatus(args.status))
            if not todos:
                print("No tasks found")
                return
            table = [
                [
                    STATUS_TO_EMOJIS[todo["status"]],
                    todo["id"],
                    todo["description"],
                    todo["created_at"].strftime("%Y-%m-%d %H:%M"),
                ]
                for todo in todos
            ]
            print(make_table(["Status", "ID", "Description", "Created At"], table))
        case "add":
            todo = manager.create(args.description, TodoStatus.TODO)
            print(f"Added task {todo['id']}: {todo['description']}")
        case "mark-in-progress":
            todo = manager.update(args.id, status=TodoStatus.IN_PROGRESS)
            if todo is None:
                print("Task not found")
                return
            print(f"Marked task {todo['id']} as in progress")
        case "mark-done":
            todo = manager.update(args.id, status=TodoStatus.DONE)
            if todo is None:
                print("Task not found")
                return
            print(f"Marked task {todo['id']} as done")
        case "delete":
            manager.delete(args.id)
            print(f"Deleted task {args.id}")


manager = JsonManager("todos.json")
if __name__ == "__main__":
    main()
