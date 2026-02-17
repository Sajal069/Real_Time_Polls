import * as Types from "@/lib/types";


const DEFAULT_API_URL = "http://localhost:5000";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? DEFAULT_API_URL;


export const SOCKET_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? DEFAULT_API_URL;

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      payload && typeof payload.error === "string"
        ? payload.error
        : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload as T;
}

export async function createPoll(question: string, options: string[]) {
  const response = await fetch(`${API_BASE_URL}/api/polls`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      options,
    }),
  });

  return parseResponse<Types.PollResponse>(response);
}

export async function fetchPoll(pollId: string) {
  const response = await fetch(`${API_BASE_URL}/api/polls/${pollId}`, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });

  return parseResponse<Types.PollResponse>(response);
}

export async function submitVote(pollId: string, optionId: string) {
  const response = await fetch(`${API_BASE_URL}/api/polls/${pollId}/vote`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ optionId }),
  });

  return parseResponse<Types.PollResponse>(response);
}
