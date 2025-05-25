using System;
using System.Data.SqlClient;
using System.Security.Cryptography;
using System.Text;
using Microsoft.SqlServer.Server;

public class Sha256Hasher
{
    [SqlFunction]
    public static string ComputeSha256(string input)
    {
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] bytes = Encoding.UTF8.GetBytes(input);
            byte[] hash = sha256.ComputeHash(bytes);
            return BitConverter.ToString(hash).Replace("-", "").ToLower();
        }
    }
}

public class DatabaseHelper
{
    public static void TestConnection()
    {
        string connectionString = "Server=MSI;Database=epad35;User Id=sa;Password=1234!;";

        try
        {
            using (SqlConnection conn = new SqlConnection(connectionString))
            {
                conn.Open();
                Console.WriteLine("✅ Koneksi Berhasil!");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("❌ Error: " + ex.Message);
        }
    }
}

class Program
{
    static void Main()
    {
        // Test koneksi database
        DatabaseHelper.TestConnection();

        // Test hashing SHA-256
        string input = "password123";
        string hashed = Sha256Hasher.ComputeSha256(input);
        Console.WriteLine($"🔹 SHA-256 dari '{input}': {hashed}");
    }
}
