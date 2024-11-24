import typing
from datetime import datetime
import json
import pathlib
import enum


class TodoStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class JsonTodo(typing.TypedDict):
    id: int
    description: str
    status: TodoStatus
    created_at: datetime
    updated_at: datetime


class JsonFile(typing.TypedDict):
    todos: dict[int, JsonTodo]


class JsonManager:
    def __init__(self, path: pathlib.Path | str) -> None:
        if isinstance(path, str):
            path = pathlib.Path(path)
        self.path = path
        self.data: JsonFile = self.load()

    def load(self) -> JsonFile:
        if not self.path.exists():
            return {"todos": {}}

        try:
            with open(self.path, "r") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError:
            return {"todos": {}}

        todos = {}
        for id_str, raw_todo in raw_data.get("todos", {}).items():
            todos[int(id_str)] = JsonTodo(
                id=int(id_str),
                description=raw_todo["description"],
                status=TodoStatus(raw_todo["status"]),
                created_at=datetime.fromisoformat(raw_todo["created_at"]),
                updated_at=datetime.fromisoformat(raw_todo["updated_at"]),
            )

        return {"todos": todos}

    def save(self) -> None:
        todos = {
            todo_id: {
                "id": todo["id"],
                "description": todo["description"],
                "status": todo["status"].value,
                "created_at": todo["created_at"].isoformat(),
                "updated_at": todo["updated_at"].isoformat(),
            }
            for todo_id, todo in self.data["todos"].items()
        }

        with open(self.path, "w") as f:
            json.dump({"todos": todos}, f, indent=4)

    def get(self, id: int, default: JsonTodo | None = None) -> JsonTodo | None:
        return self.data["todos"].get(id, default)

    def add(self, todo: JsonTodo) -> None:
        self.data["todos"][todo["id"]] = todo
        self.save()

    def update(
        self, id: int, description: str | None = None, status: TodoStatus | None = None
    ) -> JsonTodo | None:
        todo = self.get(id)
        if not todo:
            return None

        if description is not None:
            todo["description"] = description
        if status is not None:
            todo["status"] = status

        todo["updated_at"] = datetime.now()
        self.save()
        return todo

    def delete(self, id: int) -> None:
        if id in self.data["todos"]:
            del self.data["todos"][id]
            self.save()

    def get_all(self) -> list[JsonTodo]:
        return list(self.data["todos"].values())

    def get_all_by_status(self, status: TodoStatus) -> list[JsonTodo]:
        return [
            todo for todo in self.data["todos"].values() if todo["status"] == status
        ]

    def create(
        self, description: str, status: TodoStatus = TodoStatus.TODO
    ) -> JsonTodo:
        new_id = max(self.data["todos"].keys(), default=0) + 1
        now = datetime.now()

        new_todo: JsonTodo = {
            "id": new_id,
            "description": description,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

        self.add(new_todo)
        return new_todo
