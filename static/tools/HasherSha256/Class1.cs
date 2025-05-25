using System;
using System.Data.SqlTypes;
using System.Security.Cryptography;
using System.Text;
using Microsoft.SqlServer.Server;

public class SqlFunctions
{
    [SqlFunction(IsDeterministic = true, IsPrecise = true)]
    public static SqlString ComputeSha256(SqlString input)
    {
        if (input.IsNull)
            return SqlString.Null;

        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] bytes = Encoding.UTF8.GetBytes(input.Value);
            byte[] hash = sha256.ComputeHash(bytes);
            return new SqlString(BitConverter.ToString(hash).Replace("-", "").ToLower());
        }
    }
}
