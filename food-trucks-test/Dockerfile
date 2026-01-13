# STAGE 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

RUN dotnet new webapi -n FoodTruckApi --no-openapi false
WORKDIR /app/FoodTruckApi
RUN dotnet add package Swashbuckle.AspNetCore --version 6.5.0

COPY data/ ./data/

COPY <<EOF Program.cs
using Microsoft.AspNetCore.Mvc;
using System.IO;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.MapGet("/api/food_trucks/search", ([FromQuery] string? name, [FromQuery] string? street, [FromQuery] string? location, [FromQuery] double? lat, [FromQuery] double? lon) =>
{
    // PERFORMANCE TEST VALIDATION
    if (lat.HasValue && (lat > 90 || lat < -90)) return Results.BadRequest("Invalid Latitude");
    if (lon.HasValue && (lon > 180 || lon < -180)) return Results.BadRequest("Invalid Longitude");

    var path = Path.Combine("data", "Mobile_Food_Facility_Permit.csv");
    if (!File.Exists(path)) return Results.NotFound("CSV missing");

    var lines = File.ReadAllLines(path);
    var results = new List<object>();
    char q = (char)34;

    foreach (var line in lines.Skip(1))
    {
        var cols = line.Split(',');
        if (cols.Length > 5)
        {
            string applicant = cols[1].Trim(q);
            string locDesc = cols[4].Trim(q);
            string address = cols[5].Trim(q);

            bool matches = true;
            if (!string.IsNullOrEmpty(name) && !applicant.Contains(name, StringComparison.OrdinalIgnoreCase)) matches = false;
            if (!string.IsNullOrEmpty(street) && !address.Contains(street, StringComparison.OrdinalIgnoreCase)) matches = false;
            if (!string.IsNullOrEmpty(location) && !locDesc.Contains(location, StringComparison.OrdinalIgnoreCase)) matches = false;

            if (matches)
            {
                results.Add(new { 
                    applicant = applicant, 
                    address = address, 
                    locationDescription = locDesc 
                });
            }
        }
        if (results.Count >= 20) break;
    }
    return Results.Ok(results);
});

app.Run();
EOF

RUN dotnet publish -c Release -o /app/publish

# STAGE 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
COPY data/ ./data/
ENV ASPNETCORE_URLS="http://0.0.0.0:5000"
EXPOSE 5000
ENTRYPOINT ["dotnet", "FoodTruckApi.dll"]