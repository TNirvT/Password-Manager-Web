/**
 * @jest-environment jsdom
 */

import React from 'react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import "core-js/stable";
import "regenerator-runtime/runtime";

import PasswordManagerApp from "./../password_mngr";

const server = setupServer(
  rest.get("/search_react", (req, res, ctx) => {
    return res(ctx.json({
      id: 1010,
      url: "fakeurl.xyz",
      login: "name@email.com",
      remark: "some notes",
      password: "fake_pw123"
    }))
  }),
);

const setup = () => {
  const utils = render(<PasswordManagerApp />);
  const input = utils.getByTestId("search-input");
  return {
    input,
    ...utils,
  };
};

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test("input url and serach", async () => {
  const { input } = setup();

  fireEvent.change(input, {target: {value: "fakeurl.xyz"}});
  fireEvent.click(screen.getByRole("button"));
  // waitFor(() => screen.getByTestId("url-heading"));
  // waitFor isn't working well, the next line would be executed before intended
  await screen.findByTestId("url-heading");

  expect(screen.getByTestId("url-heading")).toHaveTextContent("URL: https://fakeurl.xyz");

  fireEvent.click(screen.getByText("Generate Password"));
  await screen.findByText("Record 1010 updated successfully!");

  expect(screen.getByTestId("message-p")).toHaveTextContent("Record 1010 updated successfully!");
});
