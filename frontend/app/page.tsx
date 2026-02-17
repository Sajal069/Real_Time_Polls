"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createPoll } from "@/lib/api";

const MIN_OPTIONS = 2;
const MAX_OPTIONS = 10;

export default function HomePage() {
  const router = useRouter();

  const [question, setQuestion] = useState("");
  const [options, setOptions] = useState(["", ""]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateOption = (index: number, value: string) => {
    setOptions((previous) => previous.map((item, i) => (i === index ? value : item)));
  };

  const removeOption = (index: number) => {
    if (options.length <= MIN_OPTIONS) {
      return;
    }
    setOptions((previous) => previous.filter((_, i) => i !== index));
  };

  const addOption = () => {
    if (options.length >= MAX_OPTIONS) {
      return;
    }
    setOptions((previous) => [...previous, ""]);
  };

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    const cleanOptions = options.map((item) => item.trim()).filter(Boolean);
    if (cleanOptions.length < MIN_OPTIONS) {
      setError("Please provide at least 2 non-empty options.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await createPoll(question, cleanOptions);
      router.push(`/poll/${response.poll.id}`);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to create poll.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="hero">
        <h1>Create a Live Poll Room</h1>
        <p>
          Ask a question, share one link, and watch vote counts update in real time.
          This app enforces one-vote fairness controls before accepting each vote.
        </p>
      </section>

      <section className="panel">
        <form onSubmit={onSubmit}>
          <label className="field-label" htmlFor="question">
            Poll question
          </label>
          <input
            id="question"
            className="text-input"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            maxLength={500}
            placeholder="What should we build next?"
            required
          />

          <div style={{ marginTop: "1rem" }}>
            <label className="field-label">Options</label>
            <div className="option-grid">
              {options.map((option, index) => (
                <div className="option-row" key={`option-${index}`}>
                  <input
                    className="option-input"
                    value={option}
                    maxLength={200}
                    onChange={(event) => updateOption(index, event.target.value)}
                    placeholder={`Option ${index + 1}`}
                    required={index < MIN_OPTIONS}
                  />
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => removeOption(index)}
                    disabled={options.length <= MIN_OPTIONS}
                    aria-label={`Remove option ${index + 1}`}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={addOption}
              disabled={options.length >= MAX_OPTIONS}
            >
              Add option
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create poll"}
            </button>
          </div>

          {error && <p className="error-text">{error}</p>}
        </form>
      </section>

      <section className="panel">
        <p className="small-note">
          Fairness controls: one vote per browser token per poll and one vote per IP hash per poll.
        </p>
      </section>
    </main>
  );
}
