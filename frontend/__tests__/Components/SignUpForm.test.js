
import React from "react";
import renderer from 'react-test-renderer';
import SignUpForm from '../../src/Components/SignUpForm'


it("Render SignUpForm", () => {
  const component = renderer.create(<SignUpForm />);
  const componentJSON = component.toJSON();
  expect(componentJSON.type).toEqual("form");
  expect(componentJSON.children.length).toEqual(4);

});