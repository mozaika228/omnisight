
import { foo } from './lib'
import bar from "./bar"

export function login(user) {
  verifyToken(user.token)
  return getUser(user.id)
}

class Service {
  start() {
    this.run()
  }
  run() {
    console.log('run')
  }
}

function helper() {
  console.log('helper')
}


/**
 * Auth interface
 */
export interface Auth {
  userId: string;
  token: string;
}

enum Status { Ok, Error }

type ID = string | number

@decorator()
export class Controller extends Service implements Runnable {
  constructor(private repo) { super(); }
  handle(req: Request): Response {
    return helper();
  }
}
