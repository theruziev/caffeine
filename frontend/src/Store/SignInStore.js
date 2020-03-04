import { action, observable } from 'mobx'
import { User } from '../api'
import UserStore from './UserStore'

class SignInStore {
  @observable isLoading = false
  @observable errors = []

  @action
  async login (data) {
    const { username, password } = data
    // this.isLoading = true
    try {
      const res = await User.login(username, password)
      UserStore.authorize(res.data)
    } catch (e) {
      const response = e.response

      if (response.status === 401) {
        this.errors = []
      } else if (response.status === 400) {
        this.errors = []
      }
    }
  }
}

export default new SignInStore()
