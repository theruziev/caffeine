
import React from "react";
import renderer from 'react-test-renderer';
import SignUpForm from '../../src/Components/SignUpForm'
import { shallow } from 'enzyme'



describe('<SignUpForm />', function () {

  it('snapshot renders', () => {
    const component = renderer.create(<SignUpForm/>);
    let componentJSON = component.toJSON();
    expect(componentJSON).toMatchSnapshot();
  });

  it('render 2 input', () => {
    const component = shallow(<SignUpForm/>);
    expect(component.find('input').length).toEqual(3);
  });


})
