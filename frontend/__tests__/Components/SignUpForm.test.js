
import React from "react";

import SignUpForm from '../../src/Components/SignUpForm'
import { render, cleanup, fireEvent } from '@testing-library/react'


afterEach(cleanup)

describe('<SignUpForm />', function () {

  it('snapshot renders', () => {
    const baseElement = render(<SignUpForm/>);
    expect(baseElement).toMatchSnapshot();
  });

  it('submit', () => {
    const onSubmit = data => {
      expect(data.username).toEqual("username@example.com");
      expect(data.password).toEqual("password$password");
      expect(data.repeatPassword).toEqual("password$password");
    }
    const {container} = render(<SignUpForm onSubmit={onSubmit}/>);
    const username = container.querySelector("input[name='username']");
    const password = container.querySelector("input[name='password']");
    const repeatPassword = container.querySelector("input[name='repeatPassword']");

    fireEvent.change(username, {target: {value: "username@example.com"}});
    fireEvent.change(password, {target: {value: "password$password"}});
    fireEvent.change(repeatPassword, {target: {value: "password$password"}});


    const form = container.querySelector("form");
    fireEvent.submit(form);

  });

})
