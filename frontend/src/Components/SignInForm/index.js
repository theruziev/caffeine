import React from 'react'

import useForm from 'react-hook-form'

export default function SignInForm (props) {
  const { register, handleSubmit, errors, setError } = useForm()
  const onSubmit = data => {
    props.onSubmit(data)
  }
  for (let error of props.errors) {
    setError(error.name, error.type, error.message)
  }

  const { submitDisabled, inputsDisabled } = props
  console.log(errors);
  return (

    <form onSubmit={handleSubmit(onSubmit)}>

      <div className='field'>
        <label className='label'>Email</label>
        <div className='control'>
          <input disabled={inputsDisabled} ref={register({ required: true })}
                 className={`input ${errors.username && 'is-danger'}`} name='username' type='text'
                 placeholder='cafe@ephiopia.com'/>
        </div>
        {errors.username && <p className='help is-danger'>{errors.username.message}</p>}
      </div>

      <div className='field'>
        <label className='label'>Password</label>
        <div className='control'>
          <input disabled={inputsDisabled} ref={register({ required: true })}
                 className={`input ${errors.password && 'is-danger'}`} name='password' type='password'
                 placeholder='You password'/>
        </div>
        {errors.password && <p className='help is-danger'>The password is required</p>}

      </div>

      <div className='field is-grouped is-grouped-right'>
        <div className='control'>
          <button className='button is-primary' type='submit' disabled={submitDisabled}>Submit</button>
        </div>
      </div>
    </form>
  )
}
