import http from 'k6/http';
import { check, group, sleep, fail } from 'k6';
import { Trend } from 'k6/metrics';

let app_execution_time = new Trend('app_execution_time');

export let options = {
  vus: 1,  // 1 user looping for 1 minute
  iterations: 10, //Hardcoded number of iterations
};

export default () => {
  let req = http.get(`${__ENV.DOMAIN}/${__ENV.ENDPOINT}`);

  check(req, {
    'status is 200': r => r.status === 200,
  });

  app_execution_time.add(req.json('duration')*1000);

  sleep(0.1)
}