import { useMemo, useRef, useState } from "react";
import "./App.css";

const AGUI_ENDPOINT = import.meta.env.VITE_AGUI_ENDPOINT ?? "/doctorAgent/";

const initialMessages = [
  {
    id: "welcome",
    role: "assistant",
    content:
      "Soy tu asistente para Clinica Estetica. Puedo ayudarte con pacientes, recordatorios y finanzas. Escribe tu consulta para comenzar.",
  },
];

function createId(prefix) {
  return `${prefix}-${crypto.randomUUID()}`;
}

function toAgUiMessages(messages) {
  return messages
    .filter(
      (message) => message.role === "user" || message.role === "assistant",
    )
    .map((message) => ({
      id: message.id,
      role: message.role,
      content: message.content,
    }));
}

function App() {
  const [messages, setMessages] = useState(initialMessages);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [toolActivity, setToolActivity] = useState("");
  const threadIdRef = useRef(`thread-${crypto.randomUUID()}`);
  const chatViewportRef = useRef(null);

  const stats = useMemo(() => {
    const userMessages = messages.filter(
      (message) => message.role === "user",
    ).length;
    const assistantMessages = messages.filter(
      (message) => message.role === "assistant",
    ).length;
    return { userMessages, assistantMessages };
  }, [messages]);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      if (chatViewportRef.current) {
        chatViewportRef.current.scrollTop =
          chatViewportRef.current.scrollHeight;
      }
    });
  }

  function appendAssistantDelta(messageId, delta) {
    if (!delta) return;
    setMessages((current) =>
      current.map((message) =>
        message.id === messageId
          ? { ...message, content: `${message.content}${delta}` }
          : message,
      ),
    );
    scrollToBottom();
  }

  function processAgUiEvent(eventData, assistantMessageId) {
    if (
      eventData.type === "TEXT_MESSAGE_CONTENT" ||
      eventData.type === "TEXT_MESSAGE_CHUNK"
    ) {
      appendAssistantDelta(assistantMessageId, eventData.delta ?? "");
      return;
    }

    if (eventData.type === "TOOL_CALL_START") {
      setToolActivity(`Ejecutando herramienta: ${eventData.toolCallName}`);
      return;
    }

    if (eventData.type === "TOOL_CALL_RESULT") {
      setToolActivity(`Herramienta finalizada: ${eventData.toolCallId}`);
      return;
    }

    if (eventData.type === "RUN_ERROR") {
      throw new Error(
        eventData.message || "Error durante la ejecucion del agente",
      );
    }
  }

  async function streamAgUiResponse(payload, assistantMessageId) {
    const response = await fetch(AGUI_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok || !response.body) {
      throw new Error(`No se pudo conectar al agente. HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split("\n\n");
      buffer = chunks.pop() ?? "";

      for (const chunk of chunks) {
        const lines = chunk
          .split("\n")
          .map((line) => line.trim())
          .filter(Boolean);

        const dataLines = lines
          .filter((line) => line.startsWith("data:"))
          .map((line) => line.slice(5).trim());

        if (dataLines.length === 0) continue;
        const payloadRaw = dataLines.join("\n");
        if (payloadRaw === "[DONE]") continue;

        try {
          const eventData = JSON.parse(payloadRaw);
          processAgUiEvent(eventData, assistantMessageId);
        } catch {
          // Ignore non-JSON heartbeats or unknown payloads.
        }
      }
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isLoading) return;

    setError("");
    setToolActivity("");

    const userMessage = {
      id: createId("msg-user"),
      role: "user",
      content: trimmedPrompt,
    };
    const assistantMessage = {
      id: createId("msg-assistant"),
      role: "assistant",
      content: "",
    };

    const nextMessages = [...messages, userMessage, assistantMessage];
    setMessages(nextMessages);
    setPrompt("");
    setIsLoading(true);
    scrollToBottom();

    const payload = {
      threadId: threadIdRef.current,
      runId: `run-${crypto.randomUUID()}`,
      state: [],
      messages: toAgUiMessages(nextMessages),
      tools: [],
      context: [],
      forwardedProps: {},
    };

    try {
      await streamAgUiResponse(payload, assistantMessage.id);
    } catch (streamError) {
      const message =
        streamError instanceof Error
          ? streamError.message
          : "Ocurrio un error inesperado al consultar el agente.";

      setError(message);
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantMessage.id
            ? {
                ...item,
                content:
                  item.content ||
                  "No pude generar una respuesta por el momento.",
              }
            : item,
        ),
      );
    } finally {
      setIsLoading(false);
      setToolActivity("");
      scrollToBottom();
    }
  }

  function applyPromptSuggestion(text) {
    setPrompt(text);
  }

  return (
    <main className="app-shell">
      <section className="side-panel">
        <p className="eyebrow">Doctor Agent</p>
        <h1>Console Clinica Estetica</h1>
        <p className="lead">
          Chat operativo para gestionar pacientes, agenda de recordatorios y
          reportes financieros con respuestas en tiempo real.
        </p>

        <div className="stats-grid">
          <article className="stat-card">
            <h2>{stats.userMessages}</h2>
            <p>Mensajes usuario</p>
          </article>
          <article className="stat-card">
            <h2>{stats.assistantMessages}</h2>
            <p>Respuestas asistente</p>
          </article>
        </div>

        <div className="quick-actions">
          <p>Atajos recomendados</p>
          <button
            type="button"
            onClick={() =>
              applyPromptSuggestion(
                "Agendame recordatorios en lote para Mendez, Rivas y Paz con fecha 25-03-2026.",
              )
            }
          >
            Agenda en lote
          </button>
          <button
            type="button"
            onClick={() =>
              applyPromptSuggestion(
                "Dame un resumen financiero del mes actual con ingresos, costos y margen neto.",
              )
            }
          >
            Resumen mensual
          </button>
          <button
            type="button"
            onClick={() =>
              applyPromptSuggestion(
                "Calcula el ROI desde 01-03-2026 hasta 31-03-2026 y sugiere mejoras.",
              )
            }
          >
            Calculo de ROI
          </button>
        </div>
      </section>

      <section className="chat-panel">
        <header className="chat-header">
          <div>
            <p>AG-UI Streaming</p>
            <h2>Asistente en vivo</h2>
          </div>
          <span className={isLoading ? "status online pulse" : "status online"}>
            {isLoading ? "Pensando..." : "Disponible"}
          </span>
        </header>

        <div className="chat-viewport" ref={chatViewportRef}>
          {messages.map((message) => (
            <article
              key={message.id}
              className={`message-bubble ${message.role === "user" ? "user" : "assistant"}`}
            >
              <p className="message-role">
                {message.role === "user" ? "Tu" : "Asistente"}
              </p>
              <p className="message-content">{message.content || "..."}</p>
            </article>
          ))}
        </div>

        {toolActivity && <p className="tool-activity">{toolActivity}</p>}
        {error && <p className="error-banner">{error}</p>}

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Escribe una instruccion para el agente..."
            rows={3}
          />
          <button
            type="submit"
            disabled={isLoading || prompt.trim().length === 0}
          >
            {isLoading ? "Enviando..." : "Enviar"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default App;
