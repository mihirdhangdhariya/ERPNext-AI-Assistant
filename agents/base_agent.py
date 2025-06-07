import os
import logging
import time
import traceback
import asyncio
import faiss
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from memory.context_manager import FAISSContextManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s')

class BaseAgent:
    def __init__(self, department, tools, use_hnsw=True):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base="https://api.together.xyz/v1",
            model="meta-llama/Llama-3-70b-chat-hf",
            temperature=0.3,
            max_tokens=1024,  # Increased for better responses
        )
        self.department = department
        self.tools = tools

        self.context_path = f"context_data/context_{department}"
        os.makedirs(os.path.dirname(self.context_path), exist_ok=True)

        self.context_manager = FAISSContextManager(dim=768, use_hnsw=use_hnsw)
        self._load_context()

        try:
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,  # Increased for complex operations
                early_stopping_method="generate",
                return_intermediate_steps=False
            )
            logger.info(f"✅ {department} agent initialized successfully")
        except Exception as e:
            logger.error(f"⚠️ Agent initialization failed: {str(e)}")
            self.agent_executor = None

    def _load_context(self):
        try:
            if not self.context_manager.load_from_disk(self.context_path):
                logger.info(f"⚠️ No context found for {self.department}. Starting fresh.")
        except Exception as e:
            logger.error(f"Context loading failed: {str(e)}")
            self.context_manager.index = faiss.IndexFlatL2(self.context_manager.dim)

    def get_context_stats(self) -> dict:
        """Return info about memory size and FAISS index."""
        return {
            "entries": len(self.context_manager.context_data),
            "vectors": self.context_manager.index.ntotal,
            "dimensions": self.context_manager.dim
        }

    def run(self, query):
        if not self.agent_executor:
            return "⚠️ Agent is not properly initialized", []

        context_entries = self.context_manager.get_context(query, self.department, k=2)
        start_time = time.time()
        try:
            context_str = self._format_context(context_entries)
            full_query = f"{context_str}Current Question: {query}"
            logger.info(f"Agent input: {full_query}")
            result = asyncio.run(self._invoke_with_timeout(
                {"input": full_query},
                timeout=45  # Increased timeout
            ))
            response = result["output"]
        except asyncio.TimeoutError:
            response = "⚠️ Agent timed out. Please try a simpler query."
            logger.warning("Agent execution timed out")
        except Exception as e:
            response = f"⚠️ Agent Error: {str(e)}"
            logger.error(f"Agent execution failed: {str(e)}")
            logger.error(traceback.format_exc())
        duration = time.time() - start_time
        logger.info(f"Agent response time: {duration:.2f}s")
        if not response.startswith("⚠️"):
            self.context_manager.store_interaction(query, response, self.department)
        return response, context_entries

    async def _invoke_with_timeout(self, input, timeout=45):
        return await asyncio.wait_for(
            self.agent_executor.ainvoke(input),
            timeout=timeout
        )

    def save_context(self):
        try:
            self.context_manager.save_to_disk(self.context_path)
            return "✅ Context saved successfully"
        except Exception as e:
            return f"⚠️ Save failed: {str(e)}"

    def clear_context(self):
        self.context_manager.clear_memory()
        return "🧹 Context cleared. All historical data removed."

    def _format_context(self, context_entries):
        context_str = ""
        if context_entries:
            for entry in context_entries:
                context_str += f"Previous Q: {entry['query']}\nPrevious A: {entry['response']}\n\n"
        return context_str