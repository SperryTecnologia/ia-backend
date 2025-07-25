import { useState, useEffect, useRef } from "react";

function App() {
  const [messages, setMessages] = useState([
    { sender: "ai", text: "Olá! Pergunte o que quiser." },
  ]);
  const [input, setInput] = useState("");
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
        body: JSON.stringify({ prompt: input.trim() }),
      });

      const data = await response.json();

      const aiMsg = { sender: "ai", text: data.response || "Sem resposta da IA." };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Erro ao obter resposta da IA." },
      ]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "linear-gradient(to bottom right, #111827, #000000)",
        color: "white",
      }}
    >
      {/* Header */}
      <header
        style={{
          padding: "16px 24px",
          background: "linear-gradient(to right, #06b6d4, #3b82f6)",
          boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
        }}
      >
        <div
          style={{
            maxWidth: 1024,
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h1 style={{ fontSize: 24, fontWeight: "bold" }}>Iluy IA Chat</h1>
          <span style={{ opacity: 0.85, fontStyle: "italic", fontSize: 14 }}>
            Powered by GPT & Claude
          </span>
        </div>
      </header>

      {/* Messages */}
      <main
        style={{
          flexGrow: 1,
          overflowY: "auto",
          padding: "24px",
          maxWidth: 1024,
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              maxWidth: "80%",
              marginBottom: 16,
              padding: 16,
              borderRadius: 16,
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.sender === "user" ? "#06b6d4" : "#374151",
              color: msg.sender === "user" ? "black" : "white",
              textAlign: msg.sender === "user" ? "right" : "left",
              wordBreak: "break-word",
            }}
          >
            {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{
          display: "flex",
          gap: 8,
          padding: 16,
          maxWidth: 1024,
          margin: "0 auto 24px auto",
          width: "100%",
          boxSizing: "border-box",
        }}
      >
        <input
          type="text"
          placeholder="Digite sua mensagem..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          style={{
            flexGrow: 1,
            borderRadius: 12,
            padding: "12px 16px",
            border: "none",
            fontSize: 16,
            fontWeight: "500",
          }}
          autoComplete="off"
          spellCheck={false}
          lang="pt-BR"
        />
        <button
          type="submit"
          style={{
            backgroundColor: "#06b6d4",
            borderRadius: 12,
            padding: "12px 24px",
            fontWeight: "600",
            fontSize: 16,
            color: "black",
            border: "none",
            cursor: "pointer",
          }}
          aria-label="Enviar mensagem"
        >
          Enviar
        </button>
      </form>
    </div>
  );
}

export default App;
