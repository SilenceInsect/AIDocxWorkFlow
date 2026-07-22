"""一次性工具脚本归档目录。

当前包含：
- convert_md_to_docx.py：Markdown → DOCX 转换脚本，功能已被
  ``ai_workflow/stage_s1_input/MarkdownConverter`` 覆盖，保留为历史工具。

本目录与 ``ai_workflow/stage_*.py`` / ``ai_workflow/conversation_*.py`` 等
Pipeline 脚本平级；区别是：
- Pipeline 脚本：S1 → S8 流水线主路径
- tools/ 脚本：辅助 / 历史工具 / 一次性脚本

引用方式::

    from ai_workflow.tools import convert_md_to_docx
"""