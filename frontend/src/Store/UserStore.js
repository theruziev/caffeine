import { action, observable } from 'mobx'

class UserStore {
  @observable authorized = false
  @observable role = ''
  @observable email = ''

  @action authorize (user) {
    this.authorized = true
    this.email = user.email
    this.role = user.role
  }

  @action logout () {
    this.authorized = false
    this.email = ''
    this.role = ''
  }
}

export default new UserStore()
