
import React from "react";
import SignInForm from '../../src/Components/SignInForm'
import renderer from 'react-test-renderer';


it("Render SignInForm", () => {
  const component = renderer.create(<SignInForm />);
  const componentJSON = component.toJSON();
  expect(componentJSON.type).toEqual("form");
  expect(componentJSON.children.length).toEqual(3);

});