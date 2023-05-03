package lauchers;

import java.util.Arrays;
import java.util.Iterator;

import client.Client;
import communication.OperationMode;
import tools.Input;

public class ClientLauncher {
	
	public static void main(String[] args) throws Exception {
		
		if(!Input.isCommandLineValid(args))
			System.exit(130);
		
		Iterator<String> iter = Arrays.stream(args).iterator();
		
		int account = -1;
		String authFile = null;
		String address = null;
		int port = -1;
		String userFile = null;
		String vccFile = null;
		
		OperationMode mode = null;
		long amount = -1;
		
		while(iter.hasNext()) {
			
			String next = iter.next();
			
			if(Input.isLoneFlag(next)) {
				switch(next) {
				case "-a": //OPTION REQUIRED
					if(account != -1)
						System.exit(130);
					try {
						account = Integer.parseInt(iter.next());
					} catch(NumberFormatException e) {
						System.exit(130);
					}
					break;
				case "-s": //OPTION
					if(authFile != null)
						System.exit(130);
					authFile = iter.next();
					if(!Input.isFilenameValid(authFile))
						System.exit(130);
					break;
				case "-i": //OPTION
					if(address != null)
						System.exit(130);
					address = iter.next();
					if(!Input.isIpValid(address))
						System.exit(130);
					break;
				case "-p": //OPTION
					String strPort = iter.next();
					if(port != -1 || !Input.isPortValid(strPort))
						System.exit(130);
					try {
						port = Integer.parseInt(strPort);
					} catch(NumberFormatException e) {
						System.exit(130);
					}
					break;
				case "-u": //OPTION
					if(userFile != null)
						System.exit(130);
					userFile = iter.next();
					if(!Input.isFilenameValid(userFile))
						System.exit(130);
					break;
				case "-v": //OPTION
					if(vccFile != null)
						System.exit(130);
					vccFile = iter.next();
					if(!Input.isFilenameValid(vccFile))
						System.exit(130);
					break;
				case "-n": //MODE
					if(mode != null)
						System.exit(130);
					
					mode = OperationMode.NEW;
					try {
						String strAmount = iter.next();
						if(Input.isMoneyStringValid(strAmount)) { 
							amount = Input.moneyStringToLong(strAmount);
						} else {
							System.exit(130);
						}
					} catch(NumberFormatException e) {
						System.exit(130);
					}
					break;
				case "-d": //MODE
					if(mode != null)
						System.exit(130);
					mode = OperationMode.DEPOSIT;
					try {
						String strAmount = iter.next();
						if(Input.isMoneyStringValid(strAmount)) {
							amount = Input.moneyStringToLong(strAmount);
						} else {
							System.exit(130);
						}
					} catch(NumberFormatException e) {
						System.exit(130);
					}
					break;
				case "-c": //MODE
					if(mode != null)
						System.exit(130);
					mode = OperationMode.CREATE_VCC;
					try {
						String strAmount = iter.next();
						if(Input.isMoneyStringValid(strAmount)) {
							amount = Input.moneyStringToLong(strAmount);
						} else {
							System.exit(130);
						}
					} catch(NumberFormatException e) {
						System.exit(130);
					}
					break;
				case "-g": //MODE
					if(mode != null)
						System.exit(130);
					mode = OperationMode.GET;
					break;
				case "-m": //MODE
					if(mode != null)
						System.exit(130);
					mode = OperationMode.SHOP;
					try {
						String strAmount = iter.next();
						if(Input.isMoneyStringValid(strAmount)) {
							amount = Input.moneyStringToLong(strAmount);
						} else {
							System.exit(130);
						}
					} catch(NumberFormatException e) {
						System.exit(130);
					}
					break;
				default:
					System.exit(130);
					break;
			}
				
			} else {
				String[] separatedInput = Input.separateInput(next);
				if(separatedInput == null)
					System.exit(130);
				else {
					switch(separatedInput[0]) {
					case "-a": //OPTION REQUIRED
						if(account != -1)
							System.exit(130);
						try {
							account = Integer.parseInt(separatedInput[1]);
						} catch(NumberFormatException e) {
							System.exit(130);
						}
						break;
					case "-s": //OPTION
						if(authFile != null)
							System.exit(130);
						authFile = separatedInput[1];
						if(!Input.isFilenameValid(authFile))
							System.exit(130);
						break;
					case "-i": //OPTION
						if(address != null)
							System.exit(130);
						address = separatedInput[1];
						if(!Input.isIpValid(address))
							System.exit(130);
						break;
					case "-p": //OPTION
						String strPort = separatedInput[1];
						if(port != -1 || !Input.isPortValid(strPort))
							System.exit(130);
						try {
							port = Integer.parseInt(strPort);
						} catch(NumberFormatException e) {
							System.exit(130);
						}
						break;
					case "-u": //OPTION
						if(userFile != null)
							System.exit(130);
						userFile = separatedInput[1];
						if(!Input.isFilenameValid(userFile))
							System.exit(130);
						break;
					case "-v": //OPTION
						if(vccFile != null)
							System.exit(130);
						vccFile = separatedInput[1];
						if(!Input.isFilenameValid(vccFile))
							System.exit(130);
						break;
					case "-n": //MODE
						if(mode != null)
							System.exit(130);
						
						mode = OperationMode.NEW;
						try {
							String strAmount = separatedInput[1];
							if(Input.isMoneyStringValid(strAmount)) {
								amount = Input.moneyStringToLong(strAmount);
							} else {
								System.exit(130);
							}
						} catch(NumberFormatException e) {
							System.exit(130);
						}
						break;
					case "-d": //MODE
						if(mode != null)
							System.exit(130);
						mode = OperationMode.DEPOSIT;
						try {
							String strAmount = separatedInput[1];
							if(Input.isMoneyStringValid(strAmount)) {
								amount = Input.moneyStringToLong(strAmount);
							} else {
								System.exit(130);
							}
						} catch(NumberFormatException e) {
							System.exit(130);
						}
						break;
					case "-c": //MODE
						if(mode != null)
							System.exit(130);
						mode = OperationMode.CREATE_VCC;
						try {
							String strAmount = separatedInput[1];
							if(Input.isMoneyStringValid(strAmount)) {
								amount = Input.moneyStringToLong(strAmount);
							} else {
								System.exit(130);
							}
						} catch(NumberFormatException e) {
							System.exit(130);
						}
						break;
					case "-g": //MODE
						if(mode != null)
							System.exit(130);
						mode = OperationMode.GET;
						break;
					case "-m": //MODE
						if(mode != null)
							System.exit(130);
						mode = OperationMode.SHOP;
						try {
							String strAmount = separatedInput[1];
							if(Input.isMoneyStringValid(strAmount)) {
								amount = Input.moneyStringToLong(strAmount);
							} else {
								System.exit(130);
							}
						} catch(NumberFormatException e) {
							System.exit(130);
						}
						break;
					default:
						System.exit(130);
						break;
				}
				}
			}
		}
		Client client = new Client(mode, account, authFile, address, port, userFile, vccFile, amount);
		client.start();		 
	}
	
}