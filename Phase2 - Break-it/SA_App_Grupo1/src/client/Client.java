package client;

import java.sql.Timestamp;
import communication.OperationMode;

public class Client {
	
	private static final String DEFAULT_AUTH_FILE = "bank.auth";
	private static final String DEFAULT_ADDRESS = "127.0.0.1";
	private static final int DEFAULT_BANK_PORT = 3000;
	private static final int DEFAULT_STORE_PORT = 5000;
	
	private OperationMode mode;
	private int account;
	private String authFile;
	private String address;
	private int port;
	private String userFile;
	private String vccFile;
	private long amount;

	public Client(OperationMode mode, int account, String authFile, String address, int port, String userFile, 
			String vccFile, long amount) {		
		
		//INPUT VERIFICATION
		
		if(mode == null) { //mode not selected
			System.exit(130);
		}
		
		if(account < 0 && mode != OperationMode.SHOP) { //account number must be equal or greater than 0. Also true if option -a not used.
			System.exit(130);
		}
		
		if(authFile == null) { //auth file not specified
			authFile = DEFAULT_AUTH_FILE;
		}
			
		if(address == null) { //address not specified
			address = DEFAULT_ADDRESS;
		}
		
		if(port < 0) { ////port must be equal or greater than 0. Also true if not specified
			if(mode == OperationMode.SHOP) {
				port = DEFAULT_STORE_PORT;
			} else {
				port = DEFAULT_BANK_PORT;
			}
		}
		
		if(userFile == null) {
			userFile = account + ".user";
		}
		
		//END OF INPUT VERIFICATION
		
		this.mode = mode;
		this.account = account;
		this.authFile = authFile;
		this.address = address;
		this.port = port;
		this.userFile = userFile;
		this.vccFile = vccFile;
		this.amount = amount;
		
	}
	
	public void start() throws Exception {//
		
		if(mode == OperationMode.NEW) {
			
			if(amount < 15 ) { //initial balance must be greater than or equal to 15.00
				System.exit(130);
			}
			
			new RequestMaker().requestNew(account, authFile, address, port, userFile, amount);
			return;
		}
		
		if(mode == OperationMode.DEPOSIT) {
			
			if(amount <= 0 ) { //deposit amount must be greater than 0.00
				System.exit(130);
			}
			
			new RequestMaker().requestDeposit(account, authFile, address, port, userFile, amount);
			return;
		}
		
		if(mode == OperationMode.GET) {
			new RequestMaker().requestGet(account, authFile, address, port, userFile);
			return;
		}

		if(mode == OperationMode.CREATE_VCC) {
			
			if(amount <= 0 ) { //card amount must be greater than 0.00
				System.exit(130);
			}
			
			new RequestMaker().requestVcc(account, authFile, address, port, userFile, amount);
			return;
		}

		if(mode == OperationMode.SHOP) {
			Timestamp ts = new Timestamp(System.currentTimeMillis());
			new RequestMaker().requestShop(address, port, vccFile, amount, ts );
			return;
		}
	}

}