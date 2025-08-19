import java.util.*;

public class arrays {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.println("Enter the number of rows in 2D array: ");
        int rows = sc.nextInt();
        System.out.println("Enter the number of columns in 2D array: ");
        int cols = sc.nextInt();
        int[][] arr = new int[rows][cols];


        System.out.println("Enter the array elements of array: ");
        for(int i=0; i<rows; i++) {
            for(int j=0; j<cols; j++) {
                arr[i][j] = sc.nextInt();
            }
        }

        System.out.println("The array elements are: ");
        for(int i=0; i<rows; i++) {
            for(int j=0; j<cols; j++) {
                System.out.print(arr[i][j]+" ");
            }
            System.out.println();
        }
        sc.close();
    }
}