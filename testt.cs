import { getCurrentExtensionVersion, getExtensionName } from '@/version-control';

import { getKnexConfig } from './knexfile.js';
export interface UserActivity {
  id: string;
  session_id: string;
  user_id: string;
  vscode_state: string;
  mode: string;
  timestamp: string;
  synced: number;
  extension_name: string;
  extension_version: string;
  workspace_id: string;
  task_id: string | null;
  vs_code_usage: string;
}

export class SQLiteTracker {
  private knex: Knex;
	@@ -98,8 +112,10 @@ export class SQLiteTracker {
    }
  }

  public async getUnsyncedActivities(limit: number = 500): Promise<UserActivity[]> {
    return await this.knex<UserActivity>(USER_ACTIVITY_TABLE)
      .where('synced', false)
      .limit(limit);
  }

  public async markActivitiesAsSynced(ids: string[]): Promise<void> {
