/**
 * @jest-environment jsdom
 */

import React from "react";
import ReactDOM from "react-dom";
import { act } from 'react-dom/test-utils';

import PasswordManagerApp from "./../password_mngr";

let container;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
});

afterEach(() => {
  document.body.removeChild(container);
  container = null;
});

it("renders without crashing", () => {
  act(() => {
    ReactDOM.render(<PasswordManagerApp />, container);
  });
});
