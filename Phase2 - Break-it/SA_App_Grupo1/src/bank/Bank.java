package bank;

import java.net.ServerSocket;
import java.net.Socket;
import java.security.KeyPair;
import java.util.HashMap;

import tools.Encryption;

public class Bank {
	
		private static final String DEFAULT_FILENAME = "bank.auth";

		private int port = 3000;
		private HashMap<Integer,BankClient> clients;
		private HashMap<String,Vcc> vccs;
		private boolean loop = true;
		private ServerSocket ss = null;
		private String file;
		
		public Bank(int port, String file) {
			if(port != -1) 
				this.port = port;
			clients = new HashMap<>();
			vccs = new HashMap<>();
			
			if(file == null) {
				this.file = DEFAULT_FILENAME;
			} else {
				this.file = file;
			}
		}
		
		public  void startBank() {
					
			KeyPair kp = Encryption.generateKeyPair();
			if(!Encryption.storeKeyInFile(kp.getPublic(), file))
				System.exit(125);				
			System.out.println("created");
			System.out.flush();
			
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
					
					Thread t = new ServerThread(s, kp, clients, vccs);
					t.start();
				}
				
			}
			catch(Exception e) {
				
			}
		}

}