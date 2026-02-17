export type PollOption = {
  id: string;
  text: string;
  votes: number;
};

export type PollData = {
  id: string;
  question: string;
  createdAt: string;
  totalVotes: number;
  options: PollOption[];
};

export type ViewerState = {
  hasVoted: boolean;
  votedOptionId: string | null;
};

export type PollResponse = {
  poll: PollData;
  shareUrl: string;
  viewer: ViewerState;
};
