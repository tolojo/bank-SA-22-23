package communication;
import java.io.Serializable;
import java.security.Key;

public class VccStoredFile implements Serializable {

    private static final long serialVersionUID = -1898701543755746323L;

    private Key key;
    private String bankIp;
    private int bankPort;

    public VccStoredFile(Key key, String bankIp, int bankPort) {
        this.key = key;
        this.bankIp = bankIp;
        this.bankPort = bankPort;
    }

    public Key getKey() {
        return key;
    }

    public String getBankIp() {
        return bankIp;
    }

    public int getBankPort() {
        return bankPort;
    }



}
