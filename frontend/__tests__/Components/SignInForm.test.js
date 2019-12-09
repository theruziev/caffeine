import React from 'react'
import SignInForm from '../../src/Components/SignInForm'
import renderer from 'react-test-renderer'
import { shallow } from 'enzyme'

describe('<SignInForm />', function () {

  it('snapshot renders', () => {
    const component = renderer.create(<SignInForm/>);
    let componentJSON = component.toJSON();
    expect(componentJSON).toMatchSnapshot();
  });

  it('render 2 input', () => {
    const component = shallow(<SignInForm/>);
    expect(component.find('input').length).toEqual(2);
  });


})
