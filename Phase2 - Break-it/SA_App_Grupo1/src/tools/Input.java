package tools;

public class Input {
	
	private static final int COMMAND_LINE_MAX_LENGTH = 4096;
	private static final long MAX_NUMBER = 429496729599L;
	private static final int FILENAME_MAX_LENGTH = 127;
	private static final int MAX_PORT = 65535;
	private static final int MIN_PORT = 1024;
	
	private Input() {}
	
	public static boolean isLoneFlag(String input) {
		return input.length() == 2 && input.charAt(0) == '-';
	}
	
	public static String[] separateInput(String input) {
		if(input.length() < 3)
			return null;
		return new String[] {input.substring(0, 2), input.substring(2, input.length())};
	}
	
	public static boolean isCommandLineValid(String[] input) {
		return String.join("",input).length() <= COMMAND_LINE_MAX_LENGTH;
	}
	
	public static boolean isMoneyStringValid(String input) {
		try {
			return input.charAt(input.length() - 3) == '.' && Long.parseLong(input.substring(0, input.length() - 3) + input.substring(input.length() - 2, input.length())) <= MAX_NUMBER;
		} catch(Exception e) {
			return false;
		}
	}
	
	public static boolean isMoneyLongValid(long input, long min, boolean inclusive) {
		try {
			if(inclusive)
				return input <= MAX_NUMBER && input >= min;
			return input <= MAX_NUMBER && input > min;
		} catch(Exception e) {
			return false;
		}
	}
	
	public static boolean isFilenameValid(String input) {
		return input.length() <= FILENAME_MAX_LENGTH && input.charAt(0) != '.' && input.matches("[_\\-\\.0-9a-z]*");
	}
	
	public static boolean isPortValid(String input) {
		try {
			int port = Integer.parseInt(input);
			return port <= MAX_PORT && port >= MIN_PORT;
		} catch(Exception e) {
			return false;
		}
	}
	
	public static long moneyStringToLong(String input) {
        return Long.parseLong(input.substring(0, input.length() - 3) + input.substring(input.length() - 2, input.length()));
    }
	
	
	public static boolean isIpValid(String input) {
		return input.matches("^((25[0-5]|(2[0-4]|1\\d|[1-9]|)\\d)\\.?\\b){4}$");
	}
	
	public static String longAsMoney(long l) {
		if(l < 10) {
			return "0.0" + l;
		} else if(l < 100) {
			return "0." + l;
		} else {
			String input = "" + l;
			return input.substring(0, input.length() - 2) + "." + input.substring(input.length() - 2, input.length());
		}
	}

}
