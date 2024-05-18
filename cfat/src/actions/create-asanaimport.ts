
import { Task } from '../types';
import * as fs from 'fs';

async function createAsanaImport(tasks: Task[]): Promise<void> {
  let csv:string = '"Task", "Status" \r\n'
  const uniqueDetails = new Set<string>();
  // create a list of unique task details
  for(const task of tasks){
    const detail:string = task.detail ?? "UNDEFINED";
    if(detail !== "UNDEFINED"){
      uniqueDetails.add(detail);
    }
  }
  const arrayDetails = Array.from(uniqueDetails);
  for (const item of arrayDetails){
    csv += `"cfat - ${item}", "Not Started" \r\n`
  }
  fs.writeFileSync('./asana-import.csv', csv);
  return
}

export default createAsanaImport;
