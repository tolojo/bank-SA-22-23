package store;

import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;

public class Store  {
	
	private static final int DEFAULT_BANK_PORT = 5000;
	private static final String DEFAULT_AUTH_FILE = "bank.auth";
	
	private int port;
	private String authFile;
	private boolean loop = true;
	private ServerSocket ss;
	
	public Store(int port, String authFile) {
		if(port == -1) {
			this.port = DEFAULT_BANK_PORT;
		} else {
			this.port = port;
		}
		
		if(authFile == null) { //auth file not specified
			authFile = DEFAULT_AUTH_FILE;
		}
		
		this.authFile = authFile;
	}

	public void startStore() {
		
		Runtime.getRuntime().addShutdownHook(new Thread() {
	        @Override
	            public void run() {
	        		loop = false;
	        		try {
						ss.close();
						Thread.sleep(10000);
					} catch (Exception e) {
					}
	            }   
	        }); 
		
		try {
			ss = new ServerSocket(port);
			
			while(loop) {
				Socket s = ss.accept();
				s.setSoTimeout(10000);
				
				StoreThread t = new StoreThread(s, authFile);
				t.run();
			}
			
		} 
		catch(SocketTimeoutException se) {
			System.exit(63);
		}
		catch(Exception e) {
		}
		
	}
}