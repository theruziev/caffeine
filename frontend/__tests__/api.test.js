/**
 * @jest-environment node
 */
import { App, User } from '../src/api'
import Faker from 'faker'

describe('Api client', function () {

  describe('App', function () {

    it('info', async () => {
      const res = await App.info()
      expect(res.status).toBe(200)
      const data = res.data
      expect(data.name).toBe('caffeine')
    })

    it('health', async () => {
      const res = await App.health()
      expect(res.status).toBe(200)
      const data = res.data
      expect(data.postgresql_connection).toBe(true)
    })

  })

  describe('User', function () {
    describe('register', function () {
      it('register', async function () {
        const email = Faker.internet.exampleEmail()
        const password = Faker.internet.password()
        const captcha = Faker.internet.password()
        const res = await User.register(email, password, captcha)
        expect(res.status).toBe(200)
        expect(res.data.success).toBe(true)
      })

      it('existed email', async function () {
        const email = Faker.internet.exampleEmail()
        const password = Faker.internet.password()
        const captcha = Faker.internet.password()
        const registerResponse = await User.register(email, password, captcha)
        expect(registerResponse.status).toBe(200)
        expect(registerResponse.data.success).toBe(true)
        try {
          const res = await User.register(email, password, captcha)
          expect(false).toBe(true)
        } catch (e) {
          const response = e.response
          expect(response.status).toBe(409)
        }

      })

    })

  })
})
