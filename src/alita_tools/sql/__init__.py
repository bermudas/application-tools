from langchain_core.tools import BaseToolkit, BaseTool
from pydantic import BaseModel, create_model, FieldInfo

from .api_wrapper import SQLApiWrapper
from ..base.tool import BaseAction

name = "sql"


def get_tools(tool):
    return SQLToolkit().get_toolkit(
        selected_tools=tool['settings'].get('selected_tools', []),
        sql_config=tool['settings']['sql_config']
    ).get_tools()


class SQLToolkit(BaseToolkit):
    tools: list[BaseTool] = []

    @staticmethod
    def toolkit_config_schema() -> BaseModel:
        return create_model(
            name,
            sql_config=(SQLConfig, FieldInfo(description="SQL configuration"))
        )

    @classmethod
    def get_toolkit(cls, selected_tools: list[str] | None = None, **kwargs):
        if selected_tools is None:
            selected_tools = []
        sql_api_wrapper = SQLApiWrapper(**kwargs)
        available_tools = sql_api_wrapper.get_available_tools()
        tools = []
        for tool in available_tools:
            if selected_tools and tool["name"] not in selected_tools:
                continue
            tools.append(BaseAction(
                api_wrapper=sql_api_wrapper,
                name=tool["name"],
                description=tool["description"],
                args_schema=tool["args_schema"]
            ))
        return cls(tools=tools)

    def get_tools(self) -> list[BaseTool]:
        return self.tools