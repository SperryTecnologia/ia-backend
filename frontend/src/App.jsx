import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";

const getStoredMessages = () => {
  const stored = localStorage.getItem("debuga_messages");
  return stored ? JSON.parse(stored) : [
    { sender: "ai", text: "🤖 Olá! Eu sou a debuga.ai. Pergunte algo ou digite um comando." }
  ];
};

function App() {
  const [messages, setMessages] = useState(getStoredMessages());
  const [input, setInput] = useState("");
  const [darkMode, setDarkMode] = useState(true);
  const messagesEndRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const response = await fetch("http://10.1.1.171:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMsg.text }),
      });
      const data = await response.json();
      const aiMsg = { sender: "ai", text: data.resposta || "Sem resposta da IA." };
      setMessages((prev) => [...prev, aiMsg]);

      // Envia para o backend o histórico da interação (rota corrigida)
      await fetch("http://10.1.1.171:8000/api/historico", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: userMsg.text,
          resposta: aiMsg.text,
          agente: data.ia_usada || "desconhecido"
        })
      });

    } catch (err) {
      setMessages((prev) => [...prev, { sender: "ai", text: "⚠️ Erro ao conectar com o backend." }]);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    localStorage.setItem("debuga_messages", JSON.stringify(messages));
  }, [messages]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleTheme = () => setDarkMode((prev) => !prev);

  return (
    <div className={`${darkMode ? "bg-black text-green-400" : "bg-white text-zinc-800"} min-h-screen font-mono flex flex-col items-center px-4 py-6`}>
      <header className="text-2xl md:text-3xl font-bold mb-6 flex justify-between items-center w-full max-w-3xl">
        <div>
          <span className={darkMode ? "text-green-500" : "text-purple-700"}>debuga.ai</span> <span className="text-sm text-gray-400">CLI Chat</span>
          <Link
            to="/historico"
            className="ml-4 text-sm underline hover:text-green-300"
          >
            Ver histórico
          </Link>
        </div>
        <button
          onClick={toggleTheme}
          className="px-3 py-1 text-sm rounded border border-gray-400 hover:bg-gray-200 dark:hover:bg-zinc-800"
        >
          {darkMode ? "☀️ Claro" : "🌙 Escuro"}
        </button>
      </header>

      <div className={`w-full max-w-3xl flex-grow ${darkMode ? "bg-zinc-900 border-zinc-700" : "bg-zinc-100 border-zinc-300"} border rounded-lg shadow-lg p-4 overflow-y-auto h-[65vh] custom-scrollbar`}>
        <AnimatePresence initial={false}>
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className={`flex items-start space-x-2 my-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.sender === "ai" && (
                <div className="w-8 h-8 bg-green-500 text-black rounded-full flex items-center justify-center text-sm font-bold">
                  🤖
                </div>
              )}
              <div
                className={`px-4 py-2 rounded-lg text-sm md:text-base max-w-[80%] break-words
                  ${msg.sender === "ai"
                    ? darkMode ? "bg-zinc-800 text-green-300" : "bg-zinc-200 text-black"
                    : darkMode ? "bg-green-600 text-black" : "bg-purple-600 text-white"}`}
              >
                <span className="block">
                  {msg.sender === "user" ? <span className="text-white">$</span> : <span className="text-green-500">debuga.ai:</span>} {msg.text}
                </span>
              </div>
              {msg.sender === "user" && (
                <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  🧑
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex mt-4 w-full max-w-3xl"
      >
        <textarea
          rows={1}
          className={`flex-grow resize-none px-4 py-2 ${darkMode ? "bg-zinc-800 text-green-300 border-zinc-600" : "bg-white text-black border-zinc-400"} border rounded-l-md focus:outline-none focus:ring-2 focus:ring-green-500`}
          placeholder="Digite um comando ou pergunta..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="submit"
          className={`${darkMode ? "bg-green-600 hover:bg-green-700 text-black" : "bg-purple-600 hover:bg-purple-700 text-white"} font-bold px-4 py-2 rounded-r-md`}
        >
          Enviar
        </button>
      </form>
    </div>
  );
}

export default App;
