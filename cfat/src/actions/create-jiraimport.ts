
import { Task } from '../types';
import * as fs from 'fs';

async function createJiraImport(tasks: Task[]): Promise<void> {
  let csv:string = '"Summary", "Description", "Status" \r\n'
  for(const task of tasks){
    csv += `"cfat - ${task.category} - ${task.title}", "${task.detail}", "Open" \r\n`
  }

  fs.writeFileSync('./jira-import.csv', csv);
  return
}

export default createJiraImport;
