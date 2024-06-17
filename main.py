import sys
import json
from typing import Any


def infer_type(value: Any, model_defs: dict[str, str], parent_name: str) -> str:
    if isinstance(value, dict):
        model_name = f"{parent_name}SubModel"
        model_defs[model_name] = create_pydantic_model(model_name, value, model_defs)
        return model_name
    elif isinstance(value, list):
        if len(value) > 0:
            return f"list[{infer_type(value[0], model_defs, parent_name)}]"
        else:
            return "list[Any]"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, bool):
        return "bool"
    else:
        return "str"


def create_pydantic_model(
    name: str, data: dict[str, Any], model_defs: dict[str, str]
) -> str:
    fields = {
        k: infer_type(v, model_defs, name + k.capitalize()) for k, v in data.items()
    }
    model_code = [f"class {name.replace('-', '_')}(BaseModel):"]
    for field_name, field_type in fields.items():
        model_code.append(
            f"    {field_name.replace('-', '_')}: {field_type.replace('-', '_')}"
        )
    return "\n".join(model_code)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as file:
            json_data = file.read()
    else:
        json_data = sys.stdin.read()

    data = json.loads(json_data)
    model_defs = {}
    model_code = create_pydantic_model("Model", data, model_defs)
    print("\nfrom typing import Any\nfrom pydantic import BaseModel\n")
    for sub_model_code in model_defs.values():
        print(f"{sub_model_code}\n")
    print(f"{model_code}\n")


if __name__ == "__main__":
    main()
