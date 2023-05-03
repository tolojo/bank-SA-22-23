package lauchers;

import java.util.Arrays;
import java.util.Iterator;

import store.Store;
import tools.Input;

public class StoreLauncher {
	
	public static void main(String[] args) {
		
		if(!Input.isCommandLineValid(args))
			System.exit(135);
		
		Iterator<String> iter = Arrays.stream(args).iterator();
		int port = -1;
		String authFile = null;
		
		while(iter.hasNext()) {
			
			String next = iter.next();
			
			if(Input.isLoneFlag(next)) {
				switch(next) {
				case "-p":
					if(port != -1) 
						System.exit(135);
					try {
						String strPort = iter.next();
						if(Input.isPortValid(strPort))
							port = Integer.parseInt(strPort);
						else
							System.exit(135);
					} catch(NumberFormatException e) {
						System.exit(135);
					}
					break;
					
				case "-s":
					
					if(authFile != null )
						System.exit(135);
					
					authFile = iter.next();
					if(!Input.isFilenameValid(authFile)) 
						System.exit(135);
					break;
				default:
					System.exit(135);
					break;
				}
				
			} else {
				String[] separatedInput = Input.separateInput(next);
				if(separatedInput == null)
					System.exit(135);
				else {
					switch(separatedInput[0]) {
					case "-p":
						if(port != -1) 
							System.exit(135);
						try {
							String strPort = separatedInput[1];
							if(Input.isPortValid(strPort))
								port = Integer.parseInt(strPort);
							else
								System.exit(125);
						} catch(NumberFormatException e) {
							System.exit(135);
						}
						break;
						
					case "-s":
							
						if(authFile != null)
							System.exit(135);
						
						authFile = separatedInput[1];
						
						if(!Input.isFilenameValid(authFile)) 
							System.exit(135);
						break;
						
					default:
						System.exit(135);
						break;
					}
				}
			}
		}
		
		Store store = new Store(port, authFile); 
		store.startStore();
	}
}