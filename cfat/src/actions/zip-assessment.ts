import fs from 'fs';
import path from 'path';
import archiver from 'archiver';

async function zipAssessmentFiles(): Promise<void> {
  try {
    const output = fs.createWriteStream(path.join(process.cwd(), 'assessment.zip'));
    const archive = archiver('zip', {
      zlib: { level: 9 }, // Sets the compression level.
    });

    archive.pipe(output);

    // Add the files to the archive
    archive.file(path.join(process.cwd(), 'cfat.txt'), { name: 'cfat.txt' });
    archive.file(path.join(process.cwd(), 'cfat-checks.csv'), { name: 'cfat-checks.csv' });
    archive.file(path.join(process.cwd(), 'asana-import.csv'), { name: 'asana-import.csv' });
    archive.file(path.join(process.cwd(), 'jira-import.csv'), { name: 'jira-import.csv' });
    archive.finalize();

    console.log('Zip file created successfully!');
  } catch (err) {
    console.error('Error creating zip file:', err);
  }
}

export default zipAssessmentFiles;