from typing import Any
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

class IgnoreUserPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    def is_blacklisted(self, user_id: str) -> bool:
        """检查用户是否在黑名单中"""
        if not self.config.get("enable_blacklist", True):
            return False
            
        blacklist = self.config.get("blacklist_users", [])
        return str(user_id) in [str(uid) for uid in blacklist]

    @filter.event_message_type(filter.EventMessageType.ALL, priority=10000)
    async def block_handler(self, event: AstrMessageEvent) -> Any:
        """核心拦截逻辑"""
        user_id = event.message_obj.sender.user_id
        
        if self.is_blacklisted(user_id):
            # 【核心修复】v4版本必须显式关闭 LLM 触发并停止事件传播
            event.should_call_llm(False)
            event.stop_event()
            
            # 如果开启了日志记录，则打印拦截信息
            if self.config.get("enable_log", True):
                logger.info(f"[Blacklist] 已成功拦截来自用户 {user_id} 的消息。")
            return

    @filter.command("blacklist")
    async def blacklist_cmd(self, event: AstrMessageEvent) -> Any:
        user_id = event.message_obj.sender.user_id
        status = "在名单中" if self.is_blacklisted(user_id) else "不在名单中"
        yield event.plain_result(f"你的 ID: {user_id}\n当前状态: {status}")
