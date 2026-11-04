import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the ProtoMind evidence trail", () => {
    render(<App />);
    expect(screen.getAllByText(/ProtoMind/).length).toBeGreaterThan(0);
    expect(screen.getByText("Reverse-engineer a protocol from a capture.")).toBeInTheDocument();
    expect(screen.getByText(/Synthetic evidence, labelled as such/i)).toBeInTheDocument();
  });

  it("infers length-prefixed framing from the preset", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole("button", { name: "Length prefix" }));
    expect(screen.getAllByText("length_prefix").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/000947455420616c706861/).length).toBeGreaterThan(0);
  });
});
