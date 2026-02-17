"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { io, Socket } from "socket.io-client";

import { fetchPoll, submitVote, SOCKET_URL } from "@/lib/api";
import type { PollData, PollResponse, ViewerState } from "@/lib/types";

export default function PollPage() {
  const params = useParams<{ id: string }>();
  const pollId = typeof params.id === "string" ? params.id : "";

  const [poll, setPoll] = useState<PollData | null>(null);
  const [viewer, setViewer] = useState<ViewerState>({ hasVoted: false, votedOptionId: null });
  const [shareUrl, setShareUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingOptionId, setPendingOptionId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!pollId) {
      return;
    }

    let isMounted = true;
    let socket: Socket | null = null;

    const load = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetchPoll(pollId);
        if (!isMounted) {
          return;
        }
        setPoll(response.poll);
        setViewer(response.viewer);
        setShareUrl(response.shareUrl);
      } catch (requestError) {
        if (!isMounted) {
          return;
        }
        setError(requestError instanceof Error ? requestError.message : "Failed to load poll.");
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    const connectSocket = () => {
      socket = io(SOCKET_URL, {
        withCredentials: true,
        transports: ["websocket", "polling"],
      });

      socket.on("connect", () => {
        socket?.emit("join_poll", { pollId });
      });

      socket.on("poll_updated", (nextPoll: PollData) => {
        if (isMounted) {
          setPoll(nextPoll);
        }
      });

      socket.on("socket_error", (payload: { error?: string }) => {
        if (isMounted && payload.error) {
          setError(payload.error);
        }
      });
    };

    load();
    connectSocket();

    return () => {
      isMounted = false;
      if (socket) {
        socket.emit("leave_poll", { pollId });
        socket.disconnect();
      }
    };
  }, [pollId]);

  const canVote = useMemo(() => {
    return Boolean(poll && !viewer.hasVoted && !pendingOptionId);
  }, [poll, viewer.hasVoted, pendingOptionId]);

  const onVote = async (optionId: string) => {
    if (!pollId || !canVote) {
      return;
    }

    setError(null);
    setPendingOptionId(optionId);

    try {
      const response: PollResponse = await submitVote(pollId, optionId);
      setPoll(response.poll);
      setViewer(response.viewer);
      setShareUrl(response.shareUrl);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Vote failed.");
    } finally {
      setPendingOptionId(null);
    }
  };

  const copyShareLink = async () => {
    const url = shareUrl || (typeof window !== "undefined" ? window.location.href : "");
    if (!url) {
      return;
    }

    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1400);
    } catch {
      setError("Could not copy to clipboard.");
    }
  };

  return (
    <main className="page-shell">
      <section className="hero">
        <h1>Live Poll Room</h1>
        <p>Vote once and watch all connected viewers update instantly without page refresh.</p>
      </section>

      <section className="panel">
        {isLoading && <p>Loading poll...</p>}

        {!isLoading && error && <p className="error-text">{error}</p>}

        {!isLoading && poll && (
          <>
            <div className="meta-row">
              <span className="live-pill">
                <span className="live-dot" />
                LIVE RESULTS
              </span>
              <span className="small-note">Total votes: {poll.totalVotes}</span>
              {viewer.hasVoted && <span className="small-note">You already voted in this poll.</span>}
            </div>

            <h2 style={{ marginBottom: "0.35rem", fontFamily: "var(--font-heading), serif" }}>
              {poll.question}
            </h2>

            <div className="poll-list">
              {poll.options.map((option) => {
                const percentage =
                  poll.totalVotes > 0 ? Math.round((option.votes / poll.totalVotes) * 100) : 0;
                const isPicked = viewer.votedOptionId === option.id;

                return (
                  <article className="vote-card" key={option.id}>
                    <div className="vote-header">
                      <span className="vote-title">
                        {option.text}
                        {isPicked ? " (your vote)" : ""}
                      </span>
                      <span className="vote-count">
                        {option.votes} vote{option.votes === 1 ? "" : "s"} ({percentage}%)
                      </span>
                    </div>

                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${percentage}%` }} />
                    </div>

                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => onVote(option.id)}
                      disabled={!canVote}
                    >
                      {pendingOptionId === option.id ? "Submitting..." : "Vote"}
                    </button>
                  </article>
                );
              })}
            </div>
          </>
        )}
      </section>

      {!isLoading && poll && (
        <section className="panel">
          <p className="field-label" style={{ marginTop: 0 }}>
            Share this poll
          </p>
          <div className="share-link">
            <div className="link-chip">{shareUrl}</div>
            <button type="button" className="btn btn-secondary" onClick={copyShareLink}>
              {copied ? "Copied" : "Copy link"}
            </button>
          </div>
        </section>
      )}
    </main>
  );
}
