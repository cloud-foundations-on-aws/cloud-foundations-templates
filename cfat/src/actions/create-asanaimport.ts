
import { Task } from '../types';
import * as fs from 'fs';

async function createAsanaImport(tasks: Task[]): Promise<void> {
  let csv:string = '"Task", "Description", "Status"  \r\n'
  for(const task of tasks){
    csv += `"cfat - ${task.title}", "${task.detail} - Remediation Link: ${task.remediationLink}", "Not Started" \r\n`
  }
  fs.writeFileSync('./asana-import.csv', csv);
  return
}

export default createAsanaImport;
