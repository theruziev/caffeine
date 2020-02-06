import { action, observable } from 'mobx'

class SignInStore {

  @observable isLoading = false
  @observable errors = []

  @action login(data) {
    const {username, password} = data
    this.isLoading = true
    this.errors = []
    console.log(username)
    console.log(password)
    this.errors = [
      {name: "username", type: "bad", message: "Bad username"}
    ]

    setTimeout(() => {
      this.isLoading = false;
    }, 5000)

  }

}


export default new SignInStore()