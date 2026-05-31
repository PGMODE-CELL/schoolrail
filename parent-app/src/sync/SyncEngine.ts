import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface PendingOperation {
  id: string;
  type: 'CREATE' | 'UPDATE' | 'DELETE';
  resource: string;
  data: any;
  timestamp: number;
  retryCount: number;
}

class SyncEngine {
  private pendingQueue: PendingOperation[] = [];
  private isSyncing = false;
  private syncInterval: NodeJS.Timeout | null = null;

  constructor(private apiRequest: any) {}

  async enqueue(op: Omit<PendingOperation, 'id' | 'timestamp' | 'retryCount'>) {
    const entry: PendingOperation = {
      ...op,
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      timestamp: Date.now(),
      retryCount: 0,
    };
    this.pendingQueue.push(entry);
    await this.persistQueue();
    const state = await NetInfo.fetch();
    if (state.isConnected) this.sync();
  }

  async sync() {
    if (this.isSyncing || this.pendingQueue.length === 0) return;
    this.isSyncing = true;

    const batch = [...this.pendingQueue];
    this.pendingQueue = [];

    try {
      const response = await this.apiRequest('/sync/batch', 'POST', { operations: batch });
      const { failed } = response;
      for (const op of failed) {
        if (op.retryCount < 5) {
          op.retryCount++;
          this.pendingQueue.push(op);
        }
      }
      await this.persistQueue();
    } catch {
      this.pendingQueue = [...batch, ...this.pendingQueue];
      await this.persistQueue();
    } finally {
      this.isSyncing = false;
    }
  }

  startAutoSync(intervalMs = 30000) {
    this.syncInterval = setInterval(() => this.sync(), intervalMs);
    NetInfo.addEventListener(state => {
      if (state.isConnected) this.sync();
    });
  }

  stopAutoSync() {
    if (this.syncInterval) clearInterval(this.syncInterval);
  }

  private async persistQueue() {
    await AsyncStorage.setItem('sync_queue', JSON.stringify(this.pendingQueue));
  }

  private async loadQueue() {
    const stored = await AsyncStorage.getItem('sync_queue');
    if (stored) this.pendingQueue = JSON.parse(stored);
  }

  async initialize() {
    await this.loadQueue();
    this.startAutoSync();
  }
}

export const createSyncEngine = (apiRequest: any) => new SyncEngine(apiRequest);
