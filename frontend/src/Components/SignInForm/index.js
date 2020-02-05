import React from 'react'

import useForm from 'react-hook-form'

export default function SignInForm (props) {
  const { register, handleSubmit, errors } = useForm()
  const onSubmit = data => props.onSubmit(data)

  return (

    <form onSubmit={handleSubmit(onSubmit)}>

      <div className='field'>
        <label className='label'>Email</label>
        <div className='control'>
          <input ref={register({ required: true })} className={`input ${errors.username && 'is-danger'}`} name='username' type='text' placeholder='cafe@ephiopia.com' />
        </div>
        {errors.username && <p className='help is-danger'>Username is required</p>}
      </div>

      <div className='field'>
        <label className='label'>Password</label>
        <div className='control'>
          <input ref={register({ required: true })} className={`input ${errors.password && 'is-danger'}`} name='password' type='password' placeholder='You password' />
        </div>
        {errors.password && <p className='help is-danger'>The password is required</p>}

      </div>

      <div className='field is-grouped is-grouped-right'>
        <div className='control'>
          <button className='button is-primary' type='submit'>Submit</button>
        </div>
      </div>
    </form>
  )
}
