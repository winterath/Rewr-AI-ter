import { useState } from "react";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [hasProvidedText, setHasProvidedText] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    let newMessages = [...messages];

    if (!hasProvidedText) {
      const userMessage = {
        role: "user",
        content: "Summarize this text in one sentence: " + input,
      };
      newMessages.push(userMessage);

      const summary = await sendToBackend("Summarize this text in one sentence: " + input);
      newMessages.push({
        role: "assistant",
        content: summary,
      });

      setHasProvidedText(true);
    } else {
      const userMessage = { role: "user", content: input };
      newMessages.push(userMessage);

      const answer = await sendToBackend(input);
      newMessages.push({
        role: "assistant",
        content: answer,
      });
    }

    setMessages(newMessages);
    setInput("");
  };

  const sendToBackend = async (text) => {
    try {
      const response = await fetch("http://localhost:5000/query_post", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();
      return data.answer || "No answer received.";
    } catch (error) {
      console.error(error);
      return "Error communicating with server.";
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f9fafb", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "1rem", fontSize: "1.5rem", fontWeight: "bold" }}>KnotebookLM</div>

      <div style={{ flex: 1, overflowY: "auto", padding: "1rem" }}>
        {!hasProvidedText && (
          <p style={{ textAlign: "center", color: "#6b7280" }}>
            Provide the text you wish to ask questions about.
          </p>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} style={{ display: "flex", justifyContent: "center", marginBottom: "1rem" }}>
            <div style={{ maxWidth: "36rem", width: "100%", backgroundColor: "white", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 1px 2px rgba(0,0,0,0.1)" }}>
              <p style={{ fontWeight: msg.role === "user" ? "600" : "400" }}>{msg.content}</p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ padding: "1rem", backgroundColor: "white", borderTop: "1px solid #e5e7eb", display: "flex", justifyContent: "center" }}>
        <div style={{ maxWidth: "42rem", width: "100%", display: "flex", gap: "0.5rem" }}>
          <textarea
            style={{ flex: 1, borderRadius: "1rem", border: "1px solid #d1d5db", padding: "0.5rem", resize: "none" }}
            rows={2}
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button onClick={handleSend} style={{ padding: "0.5rem 1rem", borderRadius: "0.5rem", backgroundColor: "#3b82f6", color: "white", border: "none" }}>
            Enter
          </button>
        </div>
      </div>
    </div>
  );
}