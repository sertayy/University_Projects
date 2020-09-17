import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class Main {

    public static final String SYSCATFILE ="SysCat.txt";
    public static final int PAGESIZE = 1528;
    static PrintWriter outputStream;
    public static void main(String[] args) throws IOException {

        String inFile = "test1";
        String outFile = "output.txt";
        outputStream = new PrintWriter(outFile);
        File input = new File(inFile);
        Scanner scan = new Scanner(input);
        String typeName;
        int numOfFields;
        int primaryKey;
        while(scan.hasNextLine()){
            String command = scan.nextLine();
            String[] words = command.split(" ");
            int commandLength = words.length;
            switch (words[0]) {
                case "create":
                    if (words[1].equals("type")) {
                        typeName = words[2];
                        numOfFields = Integer.parseInt(words[3]);
                        createType(typeName, numOfFields);
                    } else {
                        typeName = words[2];
                        if(commandLength - 3 <= 10){
                            int[] recordFields = new int[commandLength - 3];
                            for (int i = 3; i < commandLength; i++) {
                                recordFields[i - 3] = Integer.parseInt(words[i]);
                            }
                            createRecord(typeName, recordFields);
                        }else{
                            System.out.println("A record can have at most 10 fields!");
                        }
                    }
                    break;
                case "delete":
                    if (words[1].equals("type")) {     //delete a type
                        typeName = words[2];
                        deleteType(typeName);
                    } else {
                        typeName = words[2];
                        primaryKey = Integer.parseInt(words[3]);
                        deleteRecord(typeName, primaryKey);
                    }
                    break;
                case "list":
                    if (words[1].equals("type")) {     //list types
                        listTypes();
                    } else {
                        typeName = words[2];
                        listRecords(typeName);
                    }
                    break;
                default:
                    typeName = words[2];
                    primaryKey = Integer.parseInt(words[3]);
                    searchRecord(typeName, primaryKey);
                    break;
            }
        }
        outputStream.flush();
        outputStream.close();
        scan.close();
    }

    public static void searchRecord(String typeName, int primaryKey) throws IOException{
        String fileName = typeName + ".txt";
        int position = findTypePosition(typeName);
        String pages = new String(readFromSysCat(position+20, 4));
        String fields = new String(readFromSysCat(position+16, 4));
        int numOfFields = new BigInteger(fields.getBytes()).intValue();
        int numOfPages = new BigInteger(pages.getBytes()).intValue();
        String pageHead;
        int numOfRecords;
        int recordPosition;
        for(int i=0; i<numOfPages; i++){
            pageHead = new String(readPageHeader(fileName, PAGESIZE*(i)));
            numOfRecords = new BigInteger(pageHead.substring(0,4).getBytes()).intValue();
            recordPosition = PAGESIZE*(i) + 8;
            for(int j=0; j<numOfRecords; j++){
                if(primaryKey == readRecords(fileName, recordPosition)) {
                    for(int k=0; k<numOfFields; k++){
                        if (k==numOfFields-1){
                            outputStream.println(readRecords(fileName, recordPosition + k*4));
                        }else{
                            outputStream.print(readRecords(fileName, recordPosition + k*4) + " ");
                        }
                    }
                    break;
                }
                recordPosition += numOfFields*4;
            }
        }
    }

    public static void deleteRecord(String typeName, int primaryKey) throws IOException{
        String fileName = typeName + ".txt";
        int position = findTypePosition(typeName);
        String pages = new String(readFromSysCat(position+20, 4));
        String fields = new String(readFromSysCat(position+16, 4));
        int numOfFields = new BigInteger(fields.getBytes()).intValue();
        int numOfPages = new BigInteger(pages.getBytes()).intValue();
        String pageHead;
        int numOfRecords;
        int recordPosition;
        for(int i=0; i<numOfPages; i++){
            pageHead = new String(readPageHeader(fileName, PAGESIZE*(i)));
            numOfRecords = new BigInteger(pageHead.substring(0,4).getBytes()).intValue();
            recordPosition = PAGESIZE*(i) + 8;
            for(int j=0; j<numOfRecords; j++){
                if(primaryKey == readRecords(fileName, recordPosition)) {
                    deleteFromPage(recordPosition, numOfFields, PAGESIZE*(i)+8, numOfRecords, fileName);
                    writePageHeader(fileName, (numOfPages-1) * 1528, numOfRecords-1, 0);
                    if(numOfRecords == 1){
                        updateNumOfPages(numOfPages-1, position+20);
                    }
                    break;
                }
                recordPosition += numOfFields*4;
            }
        }
    }

    public static void deleteFromPage(int position, int numOfFields, int firstPosition, int numOfRecords, String fileName) throws IOException{
        int temp_position = position;
        int last_position = firstPosition + (numOfRecords-1)*numOfFields*4;
        while (temp_position <= last_position) {
            if(temp_position != last_position){
                int nextPosition = temp_position + numOfFields*4;
                int[] fieldValues = readFromPage(nextPosition, numOfFields, fileName);
                writeRecord(fileName , temp_position, fieldValues);
                temp_position = nextPosition;
            }else{
                RandomAccessFile file = new RandomAccessFile(fileName, "rw");
                file.seek(temp_position);
                byte[] byte_size = new byte[numOfFields*4];
                file.write(byte_size);
                file.close();
                break;
            }
        }
    }

    public static int[] readFromPage(int position, int numOfFields, String fileName) throws IOException{
        int[] fieldValues = new int[numOfFields];
        RandomAccessFile file = new RandomAccessFile(fileName, "r");
        file.seek(position);
        for(int i=0; i<numOfFields; i++){
            fieldValues[i] = file.readInt();
        }
        file.close();
        return fieldValues;
    }

    public static void listRecords(String typeName) throws IOException{
        String fileName = typeName + ".txt";
        int position = findTypePosition(typeName);
        String pages = new String(readFromSysCat(position+20, 4));
        String fields = new String(readFromSysCat(position+16, 4));
        int numOfFields = new BigInteger(fields.getBytes()).intValue();
        int numOfPages = new BigInteger(pages.getBytes()).intValue();
        String pageHead;
        int numOfRecords;
        int recordPosition;
        for(int i=0; i<numOfPages; i++){
            pageHead = new String(readPageHeader(fileName, PAGESIZE*(i)));
            numOfRecords = new BigInteger(pageHead.substring(0,4).getBytes()).intValue();
            recordPosition = PAGESIZE*(i) + 8;
            for(int j=0; j<numOfRecords; j++){
                for(int k=0; k<numOfFields; k++){
                    if (k==numOfFields-1){
                        outputStream.println(readRecords(fileName, recordPosition + k*4));
                    }else{
                        outputStream.print(readRecords(fileName, recordPosition + k*4) + " ");
                    }
                }
                recordPosition += numOfFields*4;
            }
        }
    }

    public static int readRecords(String fileName, int position) throws IOException{
        RandomAccessFile file = new RandomAccessFile(fileName, "r");
        file.seek(position);
        int fieldValue = file.readInt();
        file.close();
        return fieldValue;
    }

    public static void createRecord(String typeName, int[] recordFields) throws IOException{
        String fileName = typeName+".txt";
        int record_position;
        int numOfFields = recordFields.length;
        final int recordFieldSize = numOfFields*4;
        int position = findTypePosition(typeName);
        String pages = new String(readFromSysCat(position+20, 4));
        int numOfPages = new BigInteger(pages.getBytes()).intValue();
        if (numOfPages == 0){
            writePageHeader(fileName, numOfPages, 1, 0);
            updateNumOfPages(numOfPages+1,position+20);
            writeRecord(fileName, 8, recordFields);
        } else{
            if(numOfPages <= 512){
                String temp = new String(readPageHeader(fileName, PAGESIZE*(numOfPages-1)));
                int numOfRecords = new BigInteger(temp.substring(0,4).getBytes()).intValue();
                int isFull = new BigInteger(temp.substring(4).getBytes()).intValue();
                if(isFull==0){
                    record_position = (PAGESIZE*(numOfPages-1)) + 8 + (numOfRecords*recordFieldSize);
                    if (record_position > PAGESIZE){
                        if(numOfPages != 512) {
                            writePageHeader(fileName, numOfPages * 1528, 1, 1);
                            updateNumOfPages(numOfPages + 1, position + 20);
                            writeRecord(fileName, numOfPages * 1528 + 8, recordFields);
                        }else{
                            System.out.println("Not enough memory to insert " + typeName + " " +
                                    "type. Can not create a new page due to the file memory restriction.");
                        }
                    }else{
                        writeRecord(fileName, record_position, recordFields);
                        numOfRecords = numOfRecords+1;
                        writePageHeader(fileName, (numOfPages-1) * 1528, numOfRecords, 0);
                    }
                }
            }
        }
    }

    public static void writeRecord(String fileName, int position, int[] recordFields)throws IOException{
        RandomAccessFile file = new RandomAccessFile(fileName, "rw");
        file.seek(position);
        for (int recordField : recordFields) {
            file.writeInt(recordField);
        }
        file.close();
    }

    public static byte[] readPageHeader(String typeFileName, int position)throws IOException{
        RandomAccessFile file = new RandomAccessFile(typeFileName, "r");
        file.seek(position);
        byte[] byte_size = new byte[8];
        file.read(byte_size);
        file.close();
        return byte_size;

    }

    public static void writePageHeader(String typeFileName, int position, int numOfRecords, int isFull) throws IOException{
        RandomAccessFile file = new RandomAccessFile(typeFileName, "rw");
        file.seek(position);
        file.writeInt(numOfRecords);
        file.writeInt(isFull);
        file.close();
    }

    public static int findTypePosition(String typeName) throws IOException {
        String adjustedTypeName = typeName + String.join("", Collections.nCopies(16-typeName.length()," "));
        int typeNum = readSysCatHeader();
        int position;
        for(int i=0; i<typeNum; i++) {
            position = 4+(i*24);
            String type = new String(readFromSysCat(position, 16));
            if (adjustedTypeName.equals(type)) {
                return position;
            }
        }
        System.out.println(typeName + " is not found.");
        return -1;
    }

    public static void createType(String typeName, int numOfFields)throws IOException{
        String typeFileName = typeName + ".txt";
        File typeFile = new File(typeFileName);
        if(typeFile.createNewFile()) { // if the type file is not created before
            File sysCat = new File(SYSCATFILE);
            RandomAccessFile file = new RandomAccessFile(typeFileName, "rw");
            file.close();
            if (sysCat.createNewFile()) {     //if the system catalog is not created before
                writeSysCatHeader(1);
                writeToSysCat(typeName, numOfFields, 4, 0);
            } else {      //if the system catalog is created before
                int typeNum = readSysCatHeader();
                int position = 4 + (typeNum * 24); //16 byte -> typeName, 4 byte -> numberOfFields, 4 byte -> numberOfPages
                writeSysCatHeader(typeNum + 1); //increases number of types in system catalog by 1
                writeToSysCat(typeName, numOfFields, position, 0);
            }
        }
        else{
            System.out.println(typeFileName + " is already created.");
        }
    }

    public static void updateNumOfPages(int numOfTypes, int position) throws IOException {
        RandomAccessFile file = new RandomAccessFile(SYSCATFILE, "rw");
        file.seek(position);
        file.writeInt(numOfTypes);
        file.close();
    }

    public static void writeSysCatHeader(int num) throws IOException {
        RandomAccessFile sysCat = new RandomAccessFile(SYSCATFILE, "rw");
        sysCat.seek(0);
        sysCat.writeInt(num);
        sysCat.close();
    }

    public static int readSysCatHeader() throws IOException {
        RandomAccessFile file = new RandomAccessFile(SYSCATFILE, "r");
        file.seek(0);
        int numOfTypes = file.readInt();
        file.close();
        return numOfTypes;
    }

    public static void writeToSysCat(String typeName, int numOfFields, int position, int numOfPages) throws IOException {
        String adjustedTypeName = typeName + String.join("", Collections.nCopies(16-typeName.length()," "));
        RandomAccessFile file = new RandomAccessFile(SYSCATFILE, "rw");
        file.seek(position);
        file.write(adjustedTypeName.getBytes());
        file.writeInt(numOfFields);
        file.writeInt(numOfPages); //numOfPages
        file.close();
    }

    public static byte[] readFromSysCat(int position, int bytes) throws IOException {
        RandomAccessFile file = new RandomAccessFile(SYSCATFILE, "r");
        file.seek(position);
        byte[] byte_size = new byte[bytes];
        file.read(byte_size);
        file.close();
        return byte_size;
    }

    public static void deleteLastTypeFromSysCat() {
        try (RandomAccessFile file = new RandomAccessFile(SYSCATFILE, "rw")) {
            file.setLength(file.length() - 24);
        } catch (IOException x) {
            System.err.println(x);
        }
    }

    public static void deleteType(String typeName)throws IOException {
        String adjustedTypeName = typeName + String.join("", Collections.nCopies(16-typeName.length()," "));
        int typeNum = readSysCatHeader();
        int position=0;
        boolean typeFound = false;
        for(int i=0; i<typeNum; i++) {
            position = 4+(i*24);
            String type = new String(readFromSysCat(position, 16));
            if (adjustedTypeName.equals(type)) {
                typeFound = true;
                break;
            }
        }
        if(!typeFound) { //if the type name cannot be found
            return;
        }

        int temp_position = position;
        int last_position = 4 + (typeNum-1)*24;
        while (temp_position < last_position + 24) {
            int nextPosition = temp_position+24;
            String temp = new String(readFromSysCat(nextPosition, 24));
            String nextTypeName = temp.substring(0, 16);
            int nextTypeFields = new BigInteger(temp.substring(16,20).getBytes()).intValue();
            int numOfPages = new BigInteger(temp.substring(20).getBytes()).intValue();
            writeToSysCat(nextTypeName, nextTypeFields, temp_position, numOfPages);
            temp_position = nextPosition;
        }
        writeSysCatHeader(typeNum-1);   //decreases number of types in system catalog by 1
        typeName+=".txt";
        File file = new File(typeName);
        boolean wasSuccessful = file.delete();
        if (!wasSuccessful) {
            System.out.println("Deleting the " + typeName + " was not successful.");
        }
        deleteLastTypeFromSysCat();
    }

    @SuppressWarnings("MismatchedQueryAndUpdateOfCollection")
    public static void listTypes() throws IOException {
        int typeNum = readSysCatHeader();
        int position;
        for (int i = 0; i < typeNum; i++) {
            position = 4 + (i * 24);
            String type = new String(readFromSysCat(position, 16));
            outputStream.println(type.trim());
        }
    }
}
