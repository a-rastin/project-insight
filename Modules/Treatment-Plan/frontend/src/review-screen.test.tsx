// @vitest-environment jsdom
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

describe("psychiatrist review screen", () => {
  it("keeps the urgent finding visible while exposing and comparing structured dose edits", async () => {
    document.body.innerHTML = '<div id="root"></div>';
    await import("./main");

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain("Urgent suicide-risk review required");
    expect(alert.textContent).toContain("action not recorded");

    const dose = screen.getByRole("group", { name: "Dose" });
    const amount = within(dose).getByRole("spinbutton", { name: "Amount" });
    expect(within(dose).getByRole("combobox", { name: "Unit" })).toBeTruthy();

    const user = userEvent.setup();
    await user.clear(amount);
    await user.type(amount, "4");

    expect(screen.getByText("Edited")).toBeTruthy();
    expect(screen.getByLabelText("Recommended value: 2")).toBeTruthy();
    expect(screen.getByRole("alert").textContent).toContain("Urgent suicide-risk review required");
  });
});
