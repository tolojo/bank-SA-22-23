package lauchers;

import java.util.Arrays;
import java.util.Iterator;

import bank.Bank;
import tools.Input;

public class BankLauncher {
	

	public static void main(String[] args) {
		
		if(!Input.isCommandLineValid(args))
			System.exit(125);
		
		Iterator<String> iter = Arrays.stream(args).iterator();
		String file = null ;
		int port = -1;
		
		while(iter.hasNext()) {
			
			String next = iter.next();
			
			if(Input.isLoneFlag(next)) {
				switch(next) {
				case "-p":
					if(port != -1) 
						System.exit(125);
					try {
						
						String strPort = iter.next();
						if(Input.isPortValid(strPort)) 
							port = Integer.parseInt(strPort);
						else
							System.exit(125);
					} catch(NumberFormatException e) {
						System.exit(125);
					}
					break;
					
				case "-s":
						
					if(file != null )
						System.exit(125);
					
					file = iter.next();
					if(!Input.isFilenameValid(file))
						System.exit(125);
						
					break;
				default:
					System.exit(125);
					break;
				}
				
			} else {
				String[] separatedInput = Input.separateInput(next);
				if(separatedInput == null)
					System.exit(125);
				else {
					switch(separatedInput[0]) {
					case "-p":
						if(port != -1) 
							System.exit(125);
						try {
							String strPort = separatedInput[1];
							if(Input.isPortValid(strPort))
								port = Integer.parseInt(strPort);
							else
								System.exit(125);
						} catch(NumberFormatException e) {
							System.exit(125);
						}
						break;
						
					case "-s":
						
						if(file != null)
							System.exit(125);
						
						file = separatedInput[1];
						
						if(!Input.isFilenameValid(file))
							System.exit(125);
						
						break;
						
					default:
						System.exit(125);
						break;
					}
				}
			}
			
		}
		Bank bank = new Bank(port, file);
		bank.startBank();
				
	}

}
