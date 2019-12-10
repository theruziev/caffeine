import React from 'react'
import SignInForm from '../../src/Components/SignInForm'
import { act, cleanup, fireEvent, render, waitForElement } from '@testing-library/react'

afterEach(cleanup)

describe('<SignInForm />', function () {

  it('snapshot renders', () => {
    const { baseElement } = render(<SignInForm/>)
    expect(baseElement).toMatchSnapshot()
  })

  it('render 2 input', () => {
    const { container } = render(<SignInForm/>)
    expect(container.querySelectorAll('input').length).toEqual(2)
  })

  it('submit empty password and username', async () => {

    const { container, getByText } = render(<SignInForm/>)

    const button = container.querySelector('button')
    fireEvent.click(button)
    const usernameError = await waitForElement(() => getByText('Username is required'))
    const passwordError = await waitForElement(() => getByText('The password is required'))
    expect(usernameError).toHaveClass("is-danger");
    expect(passwordError).toHaveClass("is-danger");
  })


})
